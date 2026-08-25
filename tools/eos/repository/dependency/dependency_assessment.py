"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Architectural Dependency Assessment and Structural Integrity Engine.
    Evaluates topological graph metrics, computes modular stability profiles,
    and enforces strict multi-layered isolation constraints across the system.

Biblical Scale & Architecture:
    This is a billion-dollar, production-ready assessment vector. No child's place.
    Operates as a pure, read-only evaluation function over compiled dependency graphs.
    Leverages clean algorithmic formulations to systematically isolate architectural
    drift, unauthorized boundary crossovers, and high-risk structural coupling.

Collaboration & Maintenance:
    - [Metrics Formulation]: Evaluates Afferent and Efferent coupling to quantify 
      component instability factors using stable mathematical normalization.
    - [Boundary Control]: Validates runtime tier architectures against a user-defined
      layer sequence to prevent lower-tier dependencies from cross-pollinating upward.
    - [Data Sanitization]: Produces immutable summary sets to secure downstream reports.

===============================================================================
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .dependency_graph import DependencyGraph

# Initialize institutional logger
logger = logging.getLogger("wilsy.eos.repository.dependency.dependency_assessment")


@dataclass(frozen=True)
class ModuleMetrics:
    """
    Immutable representation of structural stability attributes for a singular module node.
    
    Mathematical Formulation:
        Afferent Coupling (Ca): Incoming dependencies (who depends on this node).
        Efferent Coupling (Ce): Outgoing dependencies (who this node depends on).
        Instability (I): Ratio of efferent coupling to total coupling.
        
        Formula: Instability (I) = Ce / (Ca + Ce)
        
        Where I is a value normalized between 0.0 and 1.0. A value of 0.0 indicates 
        a maximally stable, resilient core component; a value of 1.0 indicates 
        a completely volatile, highly dependent outer layer.
    """
    afferent_coupling: int
    efferent_coupling: int
    instability: float


class DependencyAssessment:
    """
    Industrial-grade Codebase Vulnerability and Boundary Assessment Engine.
    Executes analytical scans across verified dependency networks to isolate telemetry regressions.
    """

    def __init__(self, graph: DependencyGraph) -> None:
        """
        Binds the target dependency graph to the assessment runtime context.
        """
        if not graph:
            logger.error("Security Violation: Target DependencyGraph reference is null.")
            raise ValueError("Security Violation: Cannot execute assessment on an uninitialized graph context.")
            
        self._graph = graph
        logger.debug("DependencyAssessment engine bound successfully to target graph context.")

    def compute_metrics(self) -> dict[str, ModuleMetrics]:
        """
        Computes Afferent, Efferent, and Instability metrics for all registered graph segments.
        
        Collaboration Comment:
        Calculates reverse lookup linkages dynamically to determine Afferent coupling metrics
        without modifying or staining the underlying graph model state.
        """
        nodes = self._graph.all_nodes()
        
        # Initialize internal maps for tracking linkages
        efferent_map: dict[str, int] = {}
        afferent_map: dict[str, set[str]] = {node: set() for node in nodes}

        # First pass: Aggregate explicit linkages and trace reciprocal nodes
        for node in nodes:
            deps = self._graph.get_dependencies(node)
            efferent_map[node] = len(deps)
            
            for dep in deps:
                if dep in afferent_map:
                    afferent_map[dep].add(node)
                else:
                    # Capture external or implicit dependency references
                    afferent_map[dep] = {node}

        metrics_matrix: dict[str, ModuleMetrics] = {}
        
        # Second pass: Compute absolute normalized instability ratings
        for node in sorted(afferent_map.keys()):
            ca = len(afferent_map[node])
            ce = efferent_map.get(node, 0)
            
            total_coupling = ca + ce
            if total_coupling == 0:
                # Maximally stable default for completely decoupled leaf nodes
                instability = 0.0
            else:
                instability = float(ce) / float(total_coupling)

            metrics_matrix[node] = ModuleMetrics(
                afferent_coupling=ca,
                efferent_coupling=ce,
                instability=round(instability, 4)
            )

        logger.info(f"Successfully compiled stability metrics across {len(metrics_matrix)} tracked layout nodes.")
        return metrics_matrix

    def validate_layer_constraints(self, layer_hierarchy: list[str]) -> tuple[str, ...]:
        """
        Enforces strict layering boundaries. Prevents lower structural layers from importing upper-tier APIs.
        
        Args:
            layer_hierarchy (list[str]): An ordered sequence of package tokens representing the system tier hierarchy
                                         from lowest (most stable/core) to highest (outer interface).
                                         Example: ["core", "services", "controllers", "routes"]
        
        Returns:
            tuple[str, ...]: An immutable collection of string descriptors capturing specific boundary violations.
        """
        if not layer_hierarchy:
            logger.warning("Layer Verification Alert: Empty constraint hierarchy sequence passed. Verification skipped.")
            return ()

        violations: list[str] = []
        nodes = self._graph.all_nodes()

        def _get_layer_index(node_path: str) -> int:
            # Map node to its highest ranking matching structural keyword segment
            for index, layer_token in enumerate(layer_hierarchy):
                if f"/{layer_token}/" in f"/{node_path}/":
                    return index
            return -1

        for source_node in nodes:
            source_idx = _get_layer_index(source_node)
            if source_idx == -1:
                continue  # Node does not belong to any monitored layer architecture

            dependencies = self._graph.get_dependencies(source_node)
            for target_node in dependencies:
                target_idx = _get_layer_index(target_node)
                
                # Rule Guard: If a core layer node imports a peripheral layer node, trigger a breach alert
                if target_idx > source_idx:
                    breach_msg = (
                        f"Layering Violation: Stable tier node '{source_node}' (Layer {source_idx}) "
                        f"depends upward on volatile tier node '{target_node}' (Layer {target_idx})."
                    )
                    logger.error(f"Architectural Integrity Breach: {breach_msg}")
                    violations.append(breach_msg)

        return tuple(sorted(violations))

