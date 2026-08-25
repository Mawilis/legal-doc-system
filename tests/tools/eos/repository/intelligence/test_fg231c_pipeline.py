"""
================================================================================
WILSY OS - ENTERPRISE OPERATING SYSTEM
================================================================================
FILE: tests/tools/eos/repository/intelligence/test_fg231c_pipeline.py
MODULE: Intelligence System Integration & FG231C Pipeline Validation
VERSION: 1.0.6
AUTHOR: Wilson Khanyezi & Wilsy OS Core Engineering Architecture Team
PURPOSE:
    Provides automated unit and integration tests for the FG231C Intelligence Pipeline.

EPITOME / ARCHITECTURAL INTENT:
    Verifies end-to-end pipeline execution and file system report persistence.

COLLABORATION NOTES:
    - Maintained by Core Architecture & Legal SaaS Platform Engineering teams.
================================================================================
"""

import os
from pathlib import Path
import pytest

from tools.eos.repository.intelligence.fg231c_pipeline import FG231CPipeline  # type: ignore


@pytest.fixture
def temp_reports_dir(tmp_path) -> Path:
    """Provides a temporary path object for report persistence testing."""
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    return reports_dir


def test_fg231c_pipeline(temp_reports_dir: Path) -> None:
    """
    Validates the FG231C Intelligence Pipeline execution and report generation.
    """
    pipeline = FG231CPipeline(reports_dir=str(temp_reports_dir))
    report_data = pipeline.run(reports_dir=str(temp_reports_dir))

    report_file = temp_reports_dir / "FG231C_Master_Report.json"
    assert report_file.exists()
    assert isinstance(report_data, dict)
    assert len(report_data) > 0
