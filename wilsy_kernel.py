"""
===============================================================================
WILSY ENGINEERING KERNEL: EXECUTIVE ORCHESTRATOR
===============================================================================
Epitome:
    WilsyKernelOrchestrator: The central nervous system of Wilsy OS.
    Executes the full repository lifecycle: Discovery, Relational Graph 
    Construction, and Institutional Health Auditing.

Biblical Scale & Architecture:
    This is the billion-dollar command interface. No child's place.
    It synchronizes the entire engineering kernel, ensuring that codebases, 
    assets, and governance structures are validated against the repository 
    blueprint in real-time.

Collaboration & Maintenance:
    - [Reliability]: Implements transactional flow control for system scanning.
    - [Architecture]: Provides a single, production-ready interface for 
      CI/CD integration.
    - [Compliance]: Triggers the Judgment Engine (HealthEngine) to enforce 
      quality gates automatically.

===============================================================================
"""

import logging
from tools.eos.repository.discovery.knowledge_graph import InstitutionalKnowledgeGraph
from tools.eos.repository.discovery.scanner import RepositoryDiscoveryScanner
from tools.eos.repository.builders.capability_graph_builder import CapabilityGraphBuilder
from tools.eos.repository.builders.ownership_graph_builder import OwnershipGraphBuilder
from tools.eos.repository.builders.dependency_graph_builder import DependencyGraphBuilder
from tools.eos.repository.builders.execution_graph_builder import ExecutionGraphBuilder
from tools.eos.repository.builders.contract_graph_builder import ContractGraphBuilder
from tools.eos.repository.health.health_engine import InstitutionalHealthEngine

# Configure high-fidelity institutional logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger("wilsy.eos.kernel.orchestrator")


class WilsyKernelOrchestrator:
    """
    [Collaboration Point]: Orchestrates the lifecycle of the Wilsy Kernel.
    """

    def __init__(self) -> None:
        self._graph = InstitutionalKnowledgeGraph()
        logger.info("Kernel initialized. Standing by for scan execution.")

    def execute_lifecycle(self) -> None:
        """
        [Executive Command]: Triggers the complete repository analysis lifecycle.
        """
        logger.info("Initiating full repository analysis lifecycle.")

        # 0. Populate the graph: Discover architectural artifacts
        scanner = RepositoryDiscoveryScanner(self._graph)
        scanner.scan(root_path=".") 
        logger.info("Discovery scan complete. Knowledge Graph populated.")

        # 1. Build Relational Graphs
        builders = [
            CapabilityGraphBuilder(self._graph),
            OwnershipGraphBuilder(self._graph),
            DependencyGraphBuilder(self._graph),
            ExecutionGraphBuilder(self._graph),
            ContractGraphBuilder(self._graph)
        ]

        for builder in builders:
            builder.build()
            logger.info(f"Built: {builder.__class__.__name__}")

        # 2. Trigger Judgment Engine
        health_engine = InstitutionalHealthEngine(self._graph)
        report = health_engine.run_audit()

        # 3. Report Institutional Status
        print(f"\n--- WILSY OS: INSTITUTIONAL STATUS REPORT ---")
        print(f"STATUS: {report.status}")
        print(f"HEALTH SCORE: {report.score}/100.0")
        print(f"VIOLATIONS: {len(report.violations)}")
        for v in report.violations:
            print(f" - {v}")
        print(f"----------------------------------------------\n")


if __name__ == "__main__":
    orchestrator = WilsyKernelOrchestrator()
    orchestrator.execute_lifecycle()
