"""
================================================================================
WILSY OS - ENTERPRISE OPERATING SYSTEM
================================================================================
FILE: tools/eos/repository/intelligence/fg231c_pipeline.py
MODULE: FG231C Master Intelligence Pipeline Orchestrator
VERSION: 1.0.6
AUTHOR: Wilson Khanyezi & Wilsy OS Core Engineering Architecture Team
PURPOSE:
    Coordinates sequential execution of all 8 core intelligence subsystem engines
    and synthesizes their telemetric outputs into the FG231C Master Executive Report.

EPITOME / ARCHITECTURAL INTENT:
    Acts as the enterprise nervous system pipeline controller. Fully supports dynamic
    output directory targeting across production environments, isolated sandbox
    runtimes, and automated pytest execution suites.

COLLABORATION NOTES:
    - Maintained by Core Architecture & Legal SaaS Platform Engineering teams.
    - Production-ready, zero placeholders, complete dynamic path propagation.
================================================================================
"""

import os
import logging
from typing import Any, Dict, Optional

from tools.eos.repository.intelligence.capability_registry.capability_registry_engine import CapabilityRegistryEngine  # type: ignore
from tools.eos.repository.intelligence.dependency_graph.dependency_graph_engine import DependencyGraphEngine  # type: ignore
from tools.eos.repository.intelligence.event_graph.event_graph_engine import EventGraphEngine  # type: ignore
from tools.eos.repository.intelligence.orchestration.orchestration_engine import OrchestrationEngine  # type: ignore
from tools.eos.repository.intelligence.governance.governance_engine import GovernanceEngine  # type: ignore
from tools.eos.repository.intelligence.prediction.prediction_engine import PredictionEngine  # type: ignore
from tools.eos.repository.intelligence.knowledge.knowledge_engine import KnowledgeEngine  # type: ignore
from tools.eos.repository.intelligence.runtime.runtime_engine import RuntimeEngine  # type: ignore
from tools.eos.repository.intelligence.report.fg231c_report_engine import FG231CReportEngine  # type: ignore

logger = logging.getLogger(__name__)


class FG231CPipeline:
    """
    Master pipeline controller for Wilsy OS FG231C Intelligence Subsystems.
    """

    def __init__(self, reports_dir: Optional[str] = None) -> None:
        """
        Initializes the FG231C Master Pipeline and instantiates all 8 subsystem engines.
        """
        self.reports_dir = reports_dir or os.path.join(os.getcwd(), "reports")
        os.makedirs(self.reports_dir, exist_ok=True)

        self.capability_engine = CapabilityRegistryEngine()
        self.dependency_engine = DependencyGraphEngine()
        self.event_engine = EventGraphEngine()
        self.orchestration_engine = OrchestrationEngine()
        self.governance_engine = GovernanceEngine()
        self.prediction_engine = PredictionEngine()
        self.knowledge_engine = KnowledgeEngine()
        self.runtime_engine = RuntimeEngine()
        self.report_engine = FG231CReportEngine(reports_dir=self.reports_dir)

    def _execute_subsystem(self, engine: Any, target_dir: str) -> Dict[str, Any]:
        """
        Safely invokes subsystem engine execution, passing target_dir if supported.
        """
        if hasattr(engine, "execute_and_save"):
            try:
                return engine.execute_and_save(reports_dir=target_dir)
            except TypeError:
                return engine.execute_and_save()
        elif hasattr(engine, "execute"):
            try:
                return engine.execute(reports_dir=target_dir)
            except TypeError:
                return engine.execute()
        elif hasattr(engine, "run"):
            try:
                return engine.run(reports_dir=target_dir)
            except TypeError:
                return engine.run()
        else:
            raise AttributeError(f"Engine {engine.__class__.__name__} lacks execution interface.")

    def run(self, reports_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes all 8 intelligence subsystem engines in sequence and produces
        the master synthesized report in the requested target directory.
        """
        target_dir = reports_dir or self.reports_dir
        os.makedirs(target_dir, exist_ok=True)

        logger.info("=================================================================")
        logger.info("   WILSY OS — FG231C ENTERPRISE NERVOUS SYSTEM PIPELINE INITIATED")
        logger.info("=================================================================")

        # 1. Capability Registry Engine
        logger.info("[1/8] Executing Capability Registry Engine...")
        cap_data = self._execute_subsystem(self.capability_engine, target_dir)

        # 2. Dependency Graph Engine
        logger.info("[2/8] Executing Dependency Graph Engine...")
        dep_data = self._execute_subsystem(self.dependency_engine, target_dir)

        # 3. Event Graph Engine
        logger.info("[3/8] Executing Event Graph Engine...")
        event_data = self._execute_subsystem(self.event_engine, target_dir)

        # 4. Orchestration Engine
        logger.info("[4/8] Executing Orchestration Engine...")
        orch_data = self._execute_subsystem(self.orchestration_engine, target_dir)

        # 5. Governance Engine
        logger.info("[5/8] Executing Governance Engine...")
        gov_data = self._execute_subsystem(self.governance_engine, target_dir)

        # 6. Prediction Engine
        logger.info("[6/8] Executing Prediction Engine...")
        pred_data = self._execute_subsystem(self.prediction_engine, target_dir)

        # 7. Knowledge Engine
        logger.info("[7/8] Executing Knowledge Engine...")
        know_data = self._execute_subsystem(self.knowledge_engine, target_dir)

        # 8. Runtime Engine
        logger.info("[8/8] Executing Runtime Engine...")
        run_data = self._execute_subsystem(self.runtime_engine, target_dir)

        # Synthesis & Master Reporting
        logger.info("Synthesizing outputs into Master Intelligence Report...")
        master_report = self.report_engine.execute_and_save(
            reports_dir=target_dir,
            capability_data=cap_data,
            dependency_data=dep_data,
            event_data=event_data,
            orchestration_data=orch_data,
            governance_data=gov_data,
            prediction_data=pred_data,
            knowledge_data=know_data,
            runtime_data=run_data,
        )

        logger.info("=================================================================")
        logger.info("   WILSY OS — FG231C ENTERPRISE NERVOUS SYSTEM PIPELINE COMPLETED")
        logger.info("=================================================================")

        return master_report
