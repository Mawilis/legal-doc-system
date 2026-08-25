"""
FG143D Integrated Runtime Tests

Verifies the complete Repository Intelligence Runtime synthesis chain.
"""

from __future__ import annotations

import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

from tools.eos.repository.application.repository_runtime import (
    RepositoryIntelligenceRuntime,
)
from tools.eos.repository.domain.models import RepositoryIntelligenceReport


class TestRepositoryIntelligenceRuntimeFG143D(unittest.TestCase):
    """
    Native FG143D runtime integration contract.
    """

    def test_execute_produces_complete_repository_intelligence_report(self) -> None:
        """
        The runtime must synthesize scanner, graph, assessment, and timestamp state.
        """
        with tempfile.TemporaryDirectory() as temporary_root:
            root = Path(temporary_root)

            package_dir = root / "sample_package"
            package_dir.mkdir()

            (package_dir / "__init__.py").write_text(
                "",
                encoding="utf-8",
            )

            (package_dir / "module.py").write_text(
                "VALUE = 1\n",
                encoding="utf-8",
            )

            (root / "config.json").write_text(
                '{"enabled": true}\n',
                encoding="utf-8",
            )

            runtime = RepositoryIntelligenceRuntime()
            report = runtime.execute(root)

            self.assertIsInstance(
                report,
                RepositoryIntelligenceReport,
            )

            self.assertIsNotNone(report.metrics)
            self.assertIsNotNone(report.graph)
            self.assertIsNotNone(report.assessment)
            self.assertIsNotNone(report.generated_at)

    def test_execute_preserves_immutable_graph_contract(self) -> None:
        """
        Runtime output must preserve the immutable graph tuple.
        """
        with tempfile.TemporaryDirectory() as temporary_root:
            root = Path(temporary_root)

            module = root / "module.py"
            module.write_text(
                "VALUE = 1\n",
                encoding="utf-8",
            )

            runtime = RepositoryIntelligenceRuntime()
            report = runtime.execute(root)

            self.assertIsInstance(
                report.graph,
                tuple,
            )

            self.assertIn(
                "module.py",
                report.graph,
            )

    def test_execute_generates_utc_timestamp(self) -> None:
        """
        Runtime synthesis must produce a valid UTC ISO-8601 timestamp.
        """
        with tempfile.TemporaryDirectory() as temporary_root:
            root = Path(temporary_root)

            (root / "module.py").write_text(
                "VALUE = 1\n",
                encoding="utf-8",
            )

            runtime = RepositoryIntelligenceRuntime()
            report = runtime.execute(root)

            parsed = datetime.fromisoformat(
                report.generated_at,
            )

            self.assertIsNotNone(parsed.tzinfo)
            self.assertEqual(
                parsed.utcoffset(),
                UTC.utcoffset(parsed),
            )

    def test_execute_metrics_and_graph_are_coherent(self) -> None:
        """
        Runtime metrics and graph must describe the same repository boundary.
        """
        with tempfile.TemporaryDirectory() as temporary_root:
            root = Path(temporary_root)

            package_dir = root / "pkg"
            package_dir.mkdir()

            (package_dir / "__init__.py").write_text(
                "",
                encoding="utf-8",
            )

            (package_dir / "service.py").write_text(
                "VALUE = 1\n",
                encoding="utf-8",
            )

            (root / "settings.json").write_text(
                "{}\n",
                encoding="utf-8",
            )

            runtime = RepositoryIntelligenceRuntime()
            report = runtime.execute(root)

            self.assertGreaterEqual(
                report.metrics.file_count,
                3,
            )

            self.assertGreaterEqual(
                report.metrics.python_module_count,
                2,
            )

            self.assertIn(
                "pkg/__init__.py",
                report.graph,
            )

            self.assertIn(
                "pkg/service.py",
                report.graph,
            )

            self.assertIn(
                "settings.json",
                report.graph,
            )

    def test_execute_assessment_is_synthesized_from_runtime_inputs(self) -> None:
        """
        The final report must contain a populated assessment produced by the runtime.
        """
        with tempfile.TemporaryDirectory() as temporary_root:
            root = Path(temporary_root)

            package_dir = root / "pkg"
            package_dir.mkdir()

            (package_dir / "__init__.py").write_text(
                "",
                encoding="utf-8",
            )

            (package_dir / "module.py").write_text(
                "VALUE = 1\n",
                encoding="utf-8",
            )

            runtime = RepositoryIntelligenceRuntime()
            report = runtime.execute(root)

            self.assertIsNotNone(report.assessment.health)
            self.assertIsNotNone(report.assessment.status)
            self.assertIsInstance(
                report.assessment.score,
                int,
            )

    def test_execute_does_not_mutate_repository(self) -> None:
        """
        The FG143D runtime path remains read-only with respect to source input.
        """
        with tempfile.TemporaryDirectory() as temporary_root:
            root = Path(temporary_root)

            module = root / "module.py"
            original_content = "VALUE = 42\n"
            module.write_text(
                original_content,
                encoding="utf-8",
            )

            runtime = RepositoryIntelligenceRuntime()
            runtime.execute(root)

            self.assertEqual(
                module.read_text(encoding="utf-8"),
                original_content,
            )


if __name__ == "__main__":
    unittest.main()
