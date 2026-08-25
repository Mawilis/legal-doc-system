"""
===============================================================================
WILSY OS — FG231A MASTER PIPELINE ORCHESTRATOR [V1.0.4]
===============================================================================
"""

from __future__ import annotations

import os
import sys
import logging
from datetime import datetime, timezone, timedelta

# Ensure workspace root is in sys.path
WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from tools.eos.repository.census.repository_census_engine import RepositoryCensusEngine
from tools.eos.repository.registry.module_registry_engine import ModuleRegistryEngine
from tools.eos.repository.registry.capability_registry_engine import CapabilityRegistryEngine
from tools.eos.repository.registry.enterprise_engine_registry import EnterpriseEngineRegistry
from tools.eos.repository.graph.dependency_graph_engine import DependencyGraphEngine
from tools.eos.repository.integration.integration_registry_engine import IntegrationRegistryEngine
from tools.eos.repository.registry.ownership_registry_engine import OwnershipRegistryEngine
from tools.eos.repository.health.repository_health_engine import RepositoryHealthEngine
from tools.eos.repository.reports.repository_twin_engine import RepositoryTwinEngine
from tools.eos.repository.registry.coverage_registry_engine import CoverageRegistryEngine
from tools.eos.repository.baseline.enterprise_baseline_engine import EnterpriseBaselineEngine
from tools.eos.repository.reports.repository_executive_report_engine import RepositoryExecutiveReportEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("WilsyOS.FG231A.PipelineOrchestrator")

def run_pipeline() -> None:
    sast_tz = timezone(timedelta(hours=2))
    start_time = datetime.now(sast_tz)

    try:
        RepositoryCensusEngine(WORKSPACE_ROOT).execute_census()
        ModuleRegistryEngine(WORKSPACE_ROOT).construct_registry()
        CapabilityRegistryEngine(WORKSPACE_ROOT).construct_capability_registry()
        EnterpriseEngineRegistry(WORKSPACE_ROOT).construct_enterprise_registry()
        DependencyGraphEngine(WORKSPACE_ROOT).construct_dependency_graph()
        IntegrationRegistryEngine(WORKSPACE_ROOT).construct_integration_registry()
        OwnershipRegistryEngine(WORKSPACE_ROOT).construct_ownership_registry()
        RepositoryHealthEngine(WORKSPACE_ROOT).evaluate_health()
        RepositoryTwinEngine(WORKSPACE_ROOT).construct_repository_twin()
        CoverageRegistryEngine(WORKSPACE_ROOT).construct_coverage_registry()
        EnterpriseBaselineEngine(WORKSPACE_ROOT).construct_enterprise_baseline()
        RepositoryExecutiveReportEngine(WORKSPACE_ROOT).generate_executive_report()

        end_time = datetime.now(sast_tz)
        duration = end_time - start_time
        logger.info(f"FG231A Pipeline Execution Completed in {duration.total_seconds():.2f} seconds")

    except Exception as e:
        logger.error(f"Critical Failure in FG231A Pipeline Execution: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    run_pipeline()