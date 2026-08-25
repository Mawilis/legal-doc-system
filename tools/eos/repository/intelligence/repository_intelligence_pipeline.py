"""
===============================================================================
WILSY OS — FG231B REPOSITORY INTELLIGENCE PIPELINE ORCHESTRATOR [V2.0.1]
===============================================================================
Epitome:
    Executes the entire FG231B 9-engine intelligence suite in strict dependency order, 
    constructing the Enterprise Knowledge Graph and live executive artifacts.

Biblical Worth Billions:
    "For which of you, intending to build a tower, sitteth not down first, and
    counteth the cost, whether he have sufficient to finish it?"
    — Luke 14:28

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/repository/intelligence/repository_intelligence_pipeline.py
===============================================================================
"""

from __future__ import annotations

import os
import sys
import logging
from datetime import datetime, timezone, timedelta

# MUST RESOLVE WORKSPACE ROOT BEFORE IMPORTING LOCAL MODULES
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "../../../.."))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from tools.eos.repository.intelligence.semantic_repository_engine import SemanticRepositoryEngine
from tools.eos.repository.intelligence.dependency_intelligence_engine import DependencyIntelligenceEngine
from tools.eos.repository.intelligence.capability_intelligence_engine import CapabilityIntelligenceEngine
from tools.eos.repository.intelligence.architecture_intelligence_engine import ArchitectureIntelligenceEngine
from tools.eos.repository.intelligence.technical_debt_engine import TechnicalDebtEngine
from tools.eos.repository.intelligence.execution_intelligence_engine import ExecutionIntelligenceEngine
from tools.eos.repository.intelligence.enterprise_search_engine import EnterpriseSearchEngine
from tools.eos.repository.intelligence.repository_intelligence_twin_engine import RepositoryIntelligenceTwinEngine
from tools.eos.repository.reports.repository_intelligence_report_engine import RepositoryIntelligenceReportEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("WilsyOS.FG231B.Pipeline")


def run_intelligence_pipeline() -> None:
    sast_tz = timezone(timedelta(hours=2))
    start_time = datetime.now(sast_tz)
    logger.info("===============================================================================")
    logger.info("WILSY OS — STARTING FG231B REPOSITORY INTELLIGENCE PIPELINE EXECUTION")
    logger.info("===============================================================================")

    try:
        logger.info("[1/9] Running Semantic Repository Engine...")
        SemanticRepositoryEngine(WORKSPACE_ROOT).build_semantic_graph()

        logger.info("[2/9] Running Enterprise Dependency Intelligence Engine...")
        DependencyIntelligenceEngine(WORKSPACE_ROOT).build_dependency_intelligence()

        logger.info("[3/9] Running Capability Intelligence Engine...")
        CapabilityIntelligenceEngine(WORKSPACE_ROOT).build_capability_knowledge()

        logger.info("[4/9] Running Architecture Intelligence Engine...")
        ArchitectureIntelligenceEngine(WORKSPACE_ROOT).build_architecture_graph()

        logger.info("[5/9] Running Technical Debt Intelligence Engine...")
        TechnicalDebtEngine(WORKSPACE_ROOT).evaluate_technical_debt()

        logger.info("[6/9] Running Execution Intelligence Engine...")
        ExecutionIntelligenceEngine(WORKSPACE_ROOT).build_execution_graph()

        logger.info("[7/9] Running Enterprise Search Intelligence Engine...")
        EnterpriseSearchEngine(WORKSPACE_ROOT).build_search_index()

        logger.info("[8/9] Running Repository Intelligence Twin Engine...")
        RepositoryIntelligenceTwinEngine(WORKSPACE_ROOT).build_intelligence_twin()

        logger.info("[9/9] Running Executive Intelligence Report Engine...")
        RepositoryIntelligenceReportEngine(WORKSPACE_ROOT).generate_report()

        duration = (datetime.now(sast_tz) - start_time).total_seconds()
        logger.info("===============================================================================")
        logger.info("FG231B INTELLIGENCE PIPELINE COMPLETED SUCCESSFULLY IN %.2f SECONDS", duration)
        logger.info("Enterprise Knowledge Graph is fully live in reports/")
        logger.info("===============================================================================")

    except Exception as e:
        logger.error("CRITICAL FAILURE IN FG231B PIPELINE: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    run_intelligence_pipeline()