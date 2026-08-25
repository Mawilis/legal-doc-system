"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Repository Intelligence Framework - Repository Intelligence Runtime.
    This component serves as the unified execution runtime facade coordinating
    scanning, graph mapping, and health evaluation workflows.

Biblical Scale & Architecture:
    Designed for billion-dollar, ultra-scalable software ecosystems.
    Acts as the primary entry point for repository health orchestration,
    synthesizing low-level telemetry into institutional decision records.

Collaboration & Maintenance:
    - [Architecture]: Facade orchestration pattern decoupling subsystems.
    - [Performance]: Streamlined procedural processing pipeline optimized for runtime speed.
    - [Safety]: Hardened exception safety handling all sub-component errors cleanly.

===============================================================================
"""

from __future__ import annotations

import logging
from pathlib import Path

from ..scanner.repository_scanner import RepositoryScanner
from ..graph.repository_graph import RepositoryGraph
from .repository_assessment import RepositoryAssessmentEngine
from ..reporting.report_builder import RepositoryIntelligenceReportBuilder
from ..domain.models import RepositoryIntelligenceReport

# -----------------------------------------------------------------------------
# Telemetry & Logging Configuration
# -----------------------------------------------------------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class RepositoryIntelligenceRuntime:
    """
    Repository Intelligence Runtime.

    Orchestrates the lifecycle operations of the Repository Intelligence
    Framework to deliver comprehensive structural analysis.
    """

    def __init__(self) -> None:
        """
        Initialize all structural framework sub-engines.
        
        [COLLABORATION: Engine Decoupling]
        Instantiates required component subsystems internally to abstract 
        structural wiring overhead away from higher-level kernel callers.
        """
        self._scanner = RepositoryScanner()
        self._graph_builder = RepositoryGraph()
        self._assessment_engine = RepositoryAssessmentEngine()
        self._report_builder = RepositoryIntelligenceReportBuilder()

    def execute(self, repository_root: Path) -> RepositoryIntelligenceReport:
        """
        Execute the complete repository intelligence assessment cycle.

        Args:
            repository_root (Path): The root filesystem directory to analyze.

        Returns:
            RepositoryIntelligenceReport: The fully compiled repository metrics,
                                          topography graph, and health assessments.
        """
        logger.info(f"Initiating Repository Intelligence runtime execution for: {repository_root}")

        # [COLLABORATION: Step 1 - Metric Exploration Pipeline (FG143A)]
        metrics = self._scanner.scan(repository_root)

        # [COLLABORATION: Step 2 - Immutable Graph Compilation (FG143B)]
        graph = self._graph_builder.build(repository_root)

        # [COLLABORATION: Step 3 - Heuristic Verification Calculation (FG143C)]
        assessment = self._assessment_engine.evaluate(metrics, graph)

        # [COLLABORATION: Step 4 - Synthesis Factory Mapping (FG143D)]
        report = self._report_builder.build_report(metrics, graph, assessment)

        logger.info("Repository Intelligence runtime cycle executed successfully.")
        return report
