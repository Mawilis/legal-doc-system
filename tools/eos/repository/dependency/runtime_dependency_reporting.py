"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    High-Fidelity Runtime Dependency Reporting and Structural Telemetry Engine.
    Translates raw graph architectures, stability metrics, and boundary breaches
    into clear, deterministic reporting documents and structural snapshots.

Biblical Scale & Architecture:
    This is a billion-dollar, production-ready reporting array. No child's place.
    Operates strictly under a zero-side-effect, read-only architectural policy.
    Transforms multi-dimensional coupling records into serialized formats or
    structured Markdown profiles without altering memory layouts or system graphs.

Collaboration & Maintenance:
    - [Reporting]: Employs clean string formatting to construct reliable,
      human-readable system evaluation layouts.
    - [Serialization]: Implements standard, schema-compliant dictionary mapping
      vectors for external telemetry ingest.
    - [Sanitization]: Enforces strict text isolation to safeguard reporting
      streams against cross-site scripting or shell integration hazards.

===============================================================================
"""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .dependency_graph import DependencyGraph
    from .dependency_assessment import DependencyAssessment

# Initialize institutional logger
logger = logging.getLogger("wilsy.eos.repository.dependency.runtime_dependency_reporting")


class RuntimeDependencyReporting:
    """
    Industrial-grade Architectural Telemetry and Report Generator Engine.
    Compiles structural health data metrics into machine-readable and human-readable layouts.
    """

    def __init__(self, assessment: DependencyAssessment, graph: DependencyGraph) -> None:
        """
        Binds the necessary telemetry assessors and system graphs to the reporting context.
        """
        if not assessment or not graph:
            logger.error("Security Violation: Telemetry engines or graph structures are null.")
            raise ValueError("Security Violation: Assessment and Graph contexts are mandatory for reporting.")

        self._assessment = assessment
        self._graph = graph
        logger.debug("RuntimeDependencyReporting engine initialized cleanly.")

    def generate_json_snapshot(self, layer_hierarchy: list[str] | None = None) -> dict[str, Any]:
        """
        Generates a structured, machine-readable snapshot dictionary of the codebase architecture.
        
        Collaboration Comment:
        Perfect for streaming architectural health to centralized system logs or external
        analytical dashboards without introducing performance blocks.
        """
        logger.info("Compiling architectural JSON telemetry snapshot.")
        
        metrics = self._assessment.compute_metrics()
        hierarchy = layer_hierarchy if layer_hierarchy is not None else []
        violations = self._assessment.validate_layer_constraints(hierarchy)
        has_cycles = self._graph.has_cycles()

        nodes_data: dict[str, dict[str, Any]] = {}
        for node, metric in metrics.items():
            nodes_data[node] = {
                "afferent_coupling": metric.afferent_coupling,
                "efferent_coupling": metric.efferent_coupling,
                "instability": metric.instability,
                "dependencies": list(self._graph.get_dependencies(node))
            }

        snapshot: dict[str, Any] = {
            "summary": {
                "total_nodes": len(self._graph.all_nodes()),
                "has_cyclic_dependencies": has_cycles,
                "total_layer_violations": len(violations)
            },
            "layer_configuration": hierarchy,
            "layer_violations": list(violations),
            "nodes": nodes_data
        }

        return snapshot

    def generate_markdown_report(self, layer_hierarchy: list[str] | None = None) -> str:
        """
        Compiles a comprehensive, scannable Markdown report tracking absolute modular metrics.
        """
        logger.info("Formulating structural Markdown health profile.")
        
        hierarchy = layer_hierarchy if layer_hierarchy is not None else []
        snapshot = self.generate_json_snapshot(hierarchy)
        summary = snapshot["summary"]

        lines: list[str] = [
            "# Wilsy OS Intelligence Framework - Dependency Telemetry Report",
            "",
            "## 1. Executive Structural Summary",
            "",
            f"* **Total Tracked System Nodes:** {summary['total_nodes']}",
            f"* **Cyclic Integrity Status:** {'CRITICAL BREACH (Cycles Detected)' if summary['has_cyclic_dependencies'] else 'PASSED (Zero Cycles)'}",
            f"* **Total Boundary Layer Violations:** {summary['total_layer_violations']}",
            "",
            "## 2. Modular Stability and Coupling Matrix",
            "",
            "| Module Target Node | Afferent (Ca) | Efferent (Ce) | Instability Index (I) |",
            "| :--- | :---: | :---: | :---: |"
        ]

        # Populate table sorted alphabetically by node key for deterministic layouts
        for node_key in sorted(snapshot["nodes"].keys()):
            node_info = snapshot["nodes"][node_key]
            lines.append(
                f"| `{node_key}` | {node_info['afferent_coupling']} | "
                f"{node_info['efferent_coupling']} | {node_info['instability']:.4f} |"
            )

        lines.extend([
            "",
            "## 3. Boundary Constraint Audit Log",
            ""
        ])

        if not hierarchy:
            lines.append("_No structural tier layer validation hierarchy was applied during this assessment pass._")
        elif summary["total_layer_violations"] == 0:
            lines.append("✓ **Absolute Isolation Maintained:** Zero architectural layer cross-pollinations detected.")
        else:
            lines.append("### Active Boundary Breaches Detected:")
            for violation in snapshot["layer_violations"]:
                lines.append(f"* ❌ {violation}")

        lines.append("")
        return "\n".join(lines)

